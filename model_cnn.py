import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau

from google.colab import drive


def main() -> None:
    
    drive.mount('/content/drive')
    
    train_directory = "/content/drive/MyDrive/mit/Capstone/facial_emotion_images/train" 
    test_directory = "/content/drive/MyDrive/mit/Capstone/facial_emotion_images/test" 
    validation_data = "/content/drive/MyDrive/mit/Capstone/facial_emotion_images/validation" 

    # Define the input shape for the images
    image_height = 48
    image_width = 48
    batch_size = 64

    # Load the VGG16 model pre-trained on ImageNet (excluding the top layers)
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(image_height, image_width, 3))

    # Freeze the base model layers (no training for the base layers)
    base_model.trainable = False

    # Build the custom model
    model = models.Sequential()

    # Add the base model (VGG16 without the fully connected layers)
    model.add(base_model)

    # Add a Global Average Pooling layer to reduce the feature map to a single vector per feature map
    model.add(layers.GlobalAveragePooling2D())

    # Add a fully connected layer with ReLU activation for better learning
    model.add(layers.Dense(128, activation='relu'))

    # Add a Dropout layer to prevent overfitting
    model.add(layers.Dropout(0.5))

    # Output layer with 4 neurons for 4 emotion classes, using softmax for multi-class classification
    model.add(layers.Dense(4, activation='softmax'))

    # Compile the model with Adam optimizer and categorical crossentropy loss
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

    # Print the model summary to see the architecture
    model.summary()

    # Set up a learning rate scheduler to reduce learning rate when the validation loss plateaus
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=0.0001)

    # Assuming you have your train and validation data generators set up (ImageDataGenerator)
    # Example of data generator setup:
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True
    )

    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_directory,  # Set your train directory path
        target_size=(image_height, image_width),
        batch_size=batch_size,
        class_mode='categorical'
    )

    validation_generator = test_datagen.flow_from_directory(
        test_directory,  # Set your validation directory path
        target_size=(image_height, image_width),
        batch_size=batch_size,
        class_mode='categorical'
    )

    # Train the model
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // batch_size,
        epochs=20,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // batch_size,
        callbacks=[reduce_lr]
    )

    # Save the trained model
    model.save('efficient_emotion_classifier_model.h5')

    # Evaluate the model on validation data
    validation_loss, validation_acc = model.evaluate(validation_generator)
    print(f'Validation Loss: {validation_loss}, Validation Accuracy: {validation_acc}')

if __name__ == "__main__":
    main()