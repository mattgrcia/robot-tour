import torch
import torch.nn as nn


class ConvAgent(nn.Module):
    def __init__(self, image_size, time_size, output_size):
        super(ConvAgent, self).__init__()
        channels, height, width = image_size

        # Adjust the number of input channels to include the time channel
        self.conv_layers = nn.Sequential(
            nn.Conv2d(channels + time_size, 16, kernel_size=5, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(16, 32, kernel_size=5, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Calculate the flattened size of the convolutional output
        convw = ((width - 4) // 2 - 4) // 2
        convh = ((height - 4) // 2 - 4) // 2
        linear_input_size = 32 * convw * convh

        # Fully connected layers
        self.fc_combined = nn.Sequential(
            nn.Linear(linear_input_size, 256), nn.ReLU(), nn.Linear(256, output_size)
        )

    def forward(self, x_img, x_time):
        # Add a batch dimension to x_img if it's not already present
        if x_img.dim() == 3:
            x_img = x_img.unsqueeze(0)  # Add batch dimension

        # Reshape and replicate x_time to match the spatial dimensions of x_img
        x_time = x_time.view(-1, 1, 1, 1).repeat(1, 1, x_img.size(2), x_img.size(3))

        # Concatenate x_time with x_img along the channel dimension
        x_combined = torch.cat((x_img, x_time), dim=1)

        # Forward through convolutional layers
        x = self.conv_layers(x_combined)
        x = x.view(x.size(0), -1)  # Flatten the output

        # Forward through fully connected layers
        x = self.fc_combined(x)
        return x
