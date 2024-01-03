import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from game_env import RobotTourEnv  # Import your custom Gym environment
from agent import ConvAgent  # Import your CNN-based RL agent


# Function to save the trained model
def save_model(agent, filename="robot_agent.pth"):
    torch.save(agent.state_dict(), filename)
    print(f"Model saved to {filename}")


def train(
    agent,
    target_agent,
    environment,
    episodes,
    save_interval=100,
    update_target_every=10,
):
    optimizer = optim.Adam(agent.parameters(), lr=0.001)
    best_reward = float("-inf")
    gamma = 0.99  # Discount factor for future rewards

    for episode in range(episodes):
        state = environment.reset()
        state_img = state["board_image"]
        state_time = torch.tensor(np.array([state["time"]]), dtype=torch.float32)

        done = False
        total_reward = 0

        while not done:
            # Assuming you're evaluating one instance at a time
            q_values = agent(
                state_img.unsqueeze(0), state_time.unsqueeze(0)
            )  # Add batch dimension
            print("Q-values shape:", q_values.shape)  # Should be [1, 7]

            # Select the action with the highest Q-value for this instance
            action = torch.argmax(
                q_values.squeeze()
            ).item()  # Squeeze to remove batch dimension
            print("Selected action:", action)

            new_state, reward, done = environment.step(action)
            new_state_img = new_state["board_image"]  # Make sure this is a tensor
            new_state_time = torch.tensor(
                np.array([new_state["time"]]), dtype=torch.float32
            )

            # Compute target Q-value
            with torch.no_grad():
                target_q = reward + gamma * torch.max(
                    target_agent(new_state_img, new_state_time)
                ) * (1 - done)

            # Compute current Q-value
            current_q = agent(state_img, state_time)[0][action]

            # Compute loss
            loss = F.mse_loss(current_q, target_q)

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_reward += reward
            state_img = new_state_img
            state_time = new_state_time

        # Update target network
        if episode % update_target_every == 0:
            target_agent.load_state_dict(agent.state_dict())

        # Saving the model conditionally or at intervals
        if total_reward > best_reward:
            best_reward = total_reward
            save_model(agent, filename=f"robot_agent_episode_{episode}.pth")

        if episode % save_interval == 0:
            save_model(agent, filename=f"robot_agent_interval_{episode}.pth")

    save_model(agent, filename="robot_agent_final.pth")


if __name__ == "__main__":
    env = RobotTourEnv()
    action_size = env.action_space.n
    print(action_size)

    # Determine the size of the image and time data from the observation space
    # These values should be adjusted based on your actual observation space
    image_size = (3, 64, 64)  # Example: 3 channels, 64x64 pixels
    time_size = 1  # Assuming 'time' is a single scalar

    # Initialize the main agent and the target agent
    agent = ConvAgent(image_size, time_size, action_size)
    target_agent = ConvAgent(image_size, time_size, action_size)

    # Make sure to pass both the agent and target_agent to the train function
    train(agent, target_agent, env, episodes=1000)
