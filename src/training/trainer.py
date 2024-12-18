import torch
from tqdm import tqdm


def train(model, train_loader, val_loader, optimizer, scheduler, num_epochs, device, patience=5):
    best_val_loss = float('inf')
    epochs_without_improvement = 0

    for epoch in range(num_epochs):
        model.train()
        running_train_loss = 0.0

        with tqdm(train_loader, desc=f"Training Epoch {epoch + 1}/{num_epochs}", unit="batch") as train_bar:
            for batch_idx, (x_train, conditioning_train) in enumerate(train_bar):
                x_train, conditioning_train = x_train.to(device), conditioning_train.to(device)

                optimizer.zero_grad()
                loss = model.nll_loss(x_train, conditioning_train)
                loss.backward()
                optimizer.step()

                running_train_loss += loss.item()
                train_bar.set_postfix(loss=running_train_loss / (batch_idx + 1))

        val_loss = evaluate(model, val_loader, device)
        print(f"Epoch [{epoch + 1}/{num_epochs}] - Validation Loss: {val_loss:.4f}")

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            print(f"Early stopping: No improvement in validation loss for {patience} epochs.")
            break


def evaluate(model, val_loader, device):
    model.eval()
    running_val_loss = 0.0

    with tqdm(val_loader, desc="Evaluating", unit="batch") as val_bar:
        with torch.no_grad():  # No gradients needed for validation
            for x_val, conditioning_val in val_bar:
                x_val, conditioning_val = x_val.to(device), conditioning_val.to(device)

                loss = model.nll_loss(x_val, conditioning_val)
                running_val_loss += loss.item()
                val_bar.set_postfix(loss=running_val_loss / (val_bar.n + 1))

    return running_val_loss / len(val_loader)
