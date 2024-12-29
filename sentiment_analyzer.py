from transformers import pipeline, PegasusForConditionalGeneration, PegasusTokenizer

class SentimentSummarizer:
    def __init__(self, model_path="trained_model", sentiment_model="distilbert-base-uncased-finetuned-sst-2-english"):
        # Load Pegasus model and tokenizer for summarization
        self.tokenizer = PegasusTokenizer.from_pretrained(model_path)
        self.model = PegasusForConditionalGeneration.from_pretrained(model_path)

        # Load sentiment analysis pipeline
        self.sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model)

    def transformer_analyzer(self, comment):
        """
        Analyze the sentiment of a single comment using DistilBERT.
        """
        transformer_result = self.sentiment_pipeline(comment)
        print(f"Transformer Result: {transformer_result}")  # Debugging
        return transformer_result[0]['label']  # Returns 'POSITIVE' or 'NEGATIVE'

    def analyze_comments(self, comments):
        """
        Analyze a list of comments and group them by sentiment.
        """
        sentiments = {"positive": [], "negative": []}

        for comment in comments:
            sentiment = self.transformer_analyzer(comment)
            if sentiment == 'POSITIVE':
                sentiments["positive"].append(comment)
            elif sentiment == 'NEGATIVE':
                sentiments["negative"].append(comment)

        num_positive = len(sentiments["positive"])
        num_negative = len(sentiments["negative"])

        print(f"Number of positive comments: {num_positive}")
        print(f"Number of negative comments: {num_negative}")

        # Generate user-friendly summary
        summary = self.generate_user_friendly_summary(sentiments, num_positive, num_negative)


        return sentiments, num_positive, num_negative

    def generate_user_friendly_summary(self, sentiment_groups, num_positive, num_negative):
        """
        Generate a cohesive summary based on sentiment groups and counts.
        """
        summaries = {}

        for sentiment, group_comments in sentiment_groups.items():
            if group_comments:
                # Concatenate all comments in this sentiment group
                input_text = " ".join(group_comments)

                # Tokenize and generate summary for the group
                inputs = self.tokenizer(input_text, max_length=512, truncation=True, padding="max_length", return_tensors="pt")
                summary_ids = self.model.generate(inputs['input_ids'], max_length=128, num_beams=5, early_stopping=True)
                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

                summaries[sentiment] = summary

        # Combine the summaries into a user-friendly format
        positive_summary = summaries.get('positive', "")
        negative_summary = summaries.get('negative', "")

        final_summary = ""
        if num_positive > num_negative:
            final_summary += f"Overall, the audience responded positively to this content."
            if positive_summary:
                final_summary += f" Many users appreciated certain aspects of the content. {positive_summary} "
            if negative_summary:
                final_summary += f"That said, a few users raised concerns. {negative_summary}"
        elif abs(num_positive - num_negative) < 2:
            final_summary += f"Audience reactions to the content were mixed."
            if positive_summary:
                final_summary += f" Some viewers shared positive feedback, highlighting its strengths. {positive_summary} "
            if negative_summary:
                final_summary += f"However, others expressed dissatisfaction or had critiques. {negative_summary}"
        elif num_negative > num_positive:
            final_summary += f"Overall, the audience appeared dissatisfied with this content."
            if negative_summary:
                final_summary += f" Many users shared their concerns and critiques. {negative_summary}"
            if positive_summary:
                final_summary += f" Nonetheless, there were viewers who found parts of it enjoyable. {positive_summary} "

        return final_summary.strip()

# Example Usage
comments = [
        "I love this! It's so creative and well-made.",
        "This video is so boring. I couldn't even finish it.",
        "Great job! I learned so much from this tutorial.",
        "The content was repetitive and poorly explained.",
        "Your editing skills are incredible. Keep it up!",
        "This felt like a complete waste of time. Very disappointing.",
    ]

summarizer = SentimentSummarizer()

