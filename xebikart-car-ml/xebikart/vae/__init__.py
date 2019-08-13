from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.layers import Conv2D, Flatten, Lambda
from tensorflow.keras.layers import Reshape, Conv2DTranspose
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.losses import mse, binary_crossentropy
from tensorflow.keras import backend as K


def create_variational_auto_encoder(input_shape, latent_dim, filters=16):
    # build encoder model
    inputs = Input(shape=input_shape, name='encoder_input')
    x = inputs
    for i in range(2):
        filters *= 2
        x = Conv2D(filters=filters,
                   kernel_size=3,
                   activation='relu',
                   strides=2,
                   padding='same')(x)

    # shape info needed to build decoder model
    shape_model = K.int_shape(x)

    # generate latent vector Q(z|X)
    x = Flatten()(x)
    x = Dense(128, activation='relu')(x)

    z_mean = Dense(latent_dim, name='z_mean')(x)
    z_log_var = Dense(latent_dim, name='z_log_var')(x)

    epsilon_std = 1.0

    def sampling(args):
        z_mean, z_log_var = args
        # extract dimensions
        batch = K.shape(z_mean)[0]
        dim = K.int_shape(z_mean)[1]
        # by default, random_normal has mean=0 and std=1.0
        epsilon = K.random_normal(shape=(batch, dim))
        return z_mean + K.exp(0.5 * z_log_var) * epsilon

    # use reparameterization trick to push the sampling out as input
    # note that "output_shape" isn't necessary with the TensorFlow backend
    z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

    # instantiate encoder model
    encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')

    # build decoder model
    latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
    x = Dense(shape_model[1] * shape_model[2] * shape_model[3], activation='relu')(latent_inputs)
    x = Reshape((shape_model[1], shape_model[2], shape_model[3]))(x)

    for i in range(2):
        x = Conv2DTranspose(filters=filters,
                            kernel_size=3,
                            activation='relu',
                            strides=2,
                            padding='same')(x)
        filters //= 2

    outputs = Conv2DTranspose(filters=int(inputs.shape[3]),
                              kernel_size=3,
                              activation='sigmoid',
                              padding='same',
                              name='decoder_output')(x)

    # instantiate decoder model
    decoder = Model(latent_inputs, outputs, name='decoder')

    # instantiate VAE model
    outputs = decoder(encoder(inputs)[2])

    # Build the variational autoencoder model
    vae = Model(inputs, outputs, name='vae')

    return vae


def custom_vae_loss(vae_model):
    def _loss(y_true, y_pred):
        # Reconstruction loss
        reconstruction_loss = mse(K.flatten(vae_model.inputs), K.flatten(vae_model.outputs))

        input_shape = vae_model.inputs[0].shape
        # we penalize the model more for the reconstruction error
        reconstruction_loss *= float(input_shape[1].value * input_shape[2].value * 10)

        # KL loss
        z_mean, z_log_var, z = vae_model.get_layer("encoder").outputs
        kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
        kl_loss = K.sum(kl_loss, axis=-1)
        kl_loss *= -0.5

        # Combine these losses
        vae_loss = K.mean(reconstruction_loss + kl_loss)

        # Add this loss to your model
        return vae_loss
    return _loss