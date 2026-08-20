import numpy as np

class ContextualMAB:
    def __init__(self, n_actions, context_dim, epsilon=0.1):
        self.n_actions = n_actions
        self.context_dim = context_dim
        self.epsilon = epsilon
        # Simple linear model per action: theta_a @ context
        self.theta = np.zeros((n_actions, context_dim))
        self.A = np.array([np.identity(context_dim) for _ in range(n_actions)])
        self.b = np.zeros((n_actions, context_dim))
        self.action_counts = np.zeros(n_actions)
    
    def select_strategy(self, context):
        context = np.array(context).reshape(-1)  # 1D vector
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            p = np.zeros(self.n_actions)
            for a in range(self.n_actions):
                theta_a = np.linalg.solve(self.A[a], self.b[a])
                # LinUCB: theta_a^T * context + sqrt(context^T * A_a^{-1} * context)
                p[a] = theta_a @ context + np.sqrt(context @ np.linalg.inv(self.A[a]) @ context)
            return np.argmax(p)
    
    def update(self, context, action, reward):
        context = np.array(context).reshape(-1)  # make 1D
        self.A[action] += np.outer(context, context)
        self.b[action] += reward * context
        self.action_counts[action] += 1

# Note: This is a simplified LinUCB. For production, we'd add confidence bounds.