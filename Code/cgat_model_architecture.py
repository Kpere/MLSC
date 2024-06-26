# -*- coding: utf-8 -*-
"""CAG Model Architecture.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_82squ4m64X5RECueT5Nvv1K5WuD9YEc
"""

# Import necessary libraries
import tensorflow as tf
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D, LSTM, GRU, TimeDistributed,
                                     Dense, MultiHeadAttention, LayerNormalization, Lambda,
                                     Flatten, Concatenate, Embedding, Reshape, Dropout, Concatenate, Reshape, Add)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping

class MultiHeadModelBuilder:
    def __init__(self, input_shape):
        self.input_shape = input_shape
        self.model = None

    def build_model(self):
        # Define model inputs
        input_layer = Input(shape=self.input_shape, name="input_layer")

        # CNN block with increased nodes
        cnn_layer = Conv1D(filters=128, kernel_size=3, activation='relu')(input_layer)
        cnn_layer = Conv1D(filters=128, kernel_size=3, activation='relu')(cnn_layer)
        cnn_output = GlobalMaxPooling1D()(cnn_layer)
        cnn_output = Dropout(0.5)(cnn_output)  # Adding dropout layer

        # Time Distributed GRU layer
        gru_output = TimeDistributed(Dense(64, activation='relu'))(input_layer)
        gru_output = Dropout(0.5)(gru_output)  # Adding dropout layer
        gru_output = GlobalMaxPooling1D()(gru_output)

        # Concatenating outputs from CNN and GRU
        concatenated = Concatenate()([cnn_output, gru_output])

        # Reshape concatenated for MultiHeadAttention
        reshaped_concatenated = Reshape((1, concatenated.shape[1]))(concatenated)

        # Multi-Head Attention layer
        attention_output = MultiHeadAttention(num_heads=2, key_dim=64)(reshaped_concatenated, reshaped_concatenated, reshaped_concatenated)

        # Reshape attention_output to match the shape of concatenated
        reshaped_attention_output = Reshape((concatenated.shape[1],))(attention_output)

        # Residual connection
        residual_output = Add()([concatenated, reshaped_attention_output])

        # Output layers
        output_layers = []
        for i in range(4):
            output_layer = Dense(3, activation='softmax', name=f"output_{i}")(residual_output)
            output_layers.append(output_layer)

        # Define model
        self.model = Model(inputs=input_layer, outputs=output_layers)

    def compile_model(self):
        # Compile model
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def train_model(self, X_train, y_train, epochs=50, batch_size=16, validation_split=0.2):
        # Early stopping callback
        early_stopping = EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)
        # Train the model
        self.history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                                       validation_split=validation_split, callbacks=[early_stopping])

    def evaluate_model(self, X_test, y_test):
        # Evaluate the model
        self.evaluation_results = self.model.evaluate(X_test, y_test)