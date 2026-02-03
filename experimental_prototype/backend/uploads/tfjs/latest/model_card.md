# Model description

The model is a convolutional neural network (CNN) that classifies satellite images into eight classes: Agricultural area, Forest, Industrial or commercial area, Railway, Residential area, Road, Square or park, and Waterbody. The model was trained on top of MobileNetV1 features, using two dense layers with 32 neurons each.

# Classes

- Agricultural area
- Forest
- Industrial or commercial area
- Railway
- Residential area
- Road
- Square or park
- Waterbody

# Model parameter

- layers: 32, 32
- epochs: 8
- batchSize: 8

# Training performance

- training loss: 0.043
- validation loss: 0.034
- training accuracy: 0.995
- validation accuracy: 1.0
- test accuracy: 0.88
