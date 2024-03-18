from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ExponentialLR
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd

class SentimentAnalyzer:
    def __init__(self, model_name, labels, epochs=3, batch_size=16, learning_rate=2e-5, lr_decay_factor=0.95):
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=len(labels))
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.softmax = torch.nn.Softmax(dim=1)
        self.labels = labels
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        self.lr_scheduler = ExponentialLR(optimizer=self.optimizer, gamma=lr_decay_factor)

    def create_dataloader(self, data):
        data = data.dropna(subset=['sentiment'])
        inputs = self.tokenizer(data['text'].astype(str).tolist(), return_tensors='pt', padding=True, truncation=True)
        sentiment_labels = torch.tensor(data['sentiment'].apply(lambda x: self.labels.index(x)).tolist())
        dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], sentiment_labels)
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

    def evaluate_model(self, predictions, true_labels):
        accuracy = accuracy_score(true_labels, predictions)
        precision = precision_score(true_labels, predictions, average='weighted')
        recall = recall_score(true_labels, predictions, average='weighted')
        f1 = f1_score(true_labels, predictions, average='weighted')
        return accuracy, precision, recall, f1

    def train(self, train_data):
        train_dataloader = self.create_dataloader(train_data)
        accumulation_steps = 4
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            for batch_idx, batch in enumerate(train_dataloader):
                input_ids, attention_mask, batch_labels = batch
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=batch_labels)
                loss = outputs.loss

                # Accumulate gradients
                loss = loss / accumulation_steps
                loss.backward()
                
                total_loss += loss.item()

                if (batch_idx + 1) % accumulation_steps == 0:
                    # Update weights after accumulation_steps mini-batches
                    self.optimizer.step()
                    self.optimizer.zero_grad()
            # Cập nhật learning rate sau mỗi epoch
            self.lr_scheduler.step()
    def evaluate(self, test_data):
        test_dataloader = self.create_dataloader(test_data)
        self.model.eval()
        true_labels = []
        predicted_labels = []
        for batch in test_dataloader:
            input_ids, attention_mask, labels = batch
            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = self.softmax(logits)
            predicted_label_index = torch.argmax(probabilities, dim=1).tolist()
            true_labels.extend(labels.tolist())
            predicted_labels.extend(predicted_label_index)
        return self.evaluate_model(predicted_labels, true_labels)

    def predict_sentiment(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probabilities = self.softmax(outputs.logits)
        predicted_label_index = torch.argmax(probabilities, dim=1).item()
        predicted_label = self.labels[predicted_label_index]
        return predicted_label

# Load train and test data
train_data = pd.read_csv('D:/PROJECT/Predict_Ietls/data/train.csv', encoding='latin1')
print(f"data training:\n {train_data}")
test_data = pd.read_csv('D:/PROJECT/Predict_Ietls/data/test.csv', encoding='latin1')
print(f"testing data:\n {test_data}")
# Define labels
labels = ['negative', 'neutral', 'positive']

# Initialize SentimentAnalyzer object
analyzer = SentimentAnalyzer(model_name="bert-base-uncased", labels=labels)

# Train the model
analyzer.train(train_data)

# Evaluate the model on test data
accuracy, precision, recall, f1 = analyzer.evaluate(test_data)
print("Test Set Performance:")
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

# Predict sentiment for a given text
text = "I love you"
predicted_sentiment = analyzer.predict_sentiment(text)
print("Predicted Sentiment:", predicted_sentiment)
