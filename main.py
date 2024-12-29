# --------------------- IMPORTS ------------------------#
import os
from config import YOUTUBE_API_KEY
from data_fetcher.youtube_fetcher import get_video_comments, get_video_id, get_youtube_details
from data_fetcher.reddit_fetcher import RedditAPI, extract_post_id
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, URL, Regexp, email, length
from sentiment_analyzer import SentimentSummarizer
from flask_mail import Message, Mail



#---------- Disable Parallelism for Hugging Face Transformers -------------#
os.environ["TOKENIZERS_PARALLELISM"] = "false"
## -------------------------FLASK SETUP--------------------------------------#
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
## -------------------------FLASK-Mail SETUP--------------------------------------#

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP server for Gmail
app.config['MAIL_PORT'] = 587  # Port for TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') # Your email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')  # Default sender for emails
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)


## ------------------------------ WTForms SEARCH SETUP ---------------------------------- ##
class SearchForm(FlaskForm):
    post_url = StringField(
        "Content URL",
        validators=[
            DataRequired(),
            URL(),
            Regexp(
                r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be|reddit\.com)/.+',
                message="Please enter a valid URL",
            ),
        ],
    )
    submit = SubmitField("Analyze")

#------------------------ RENDER HOMEPAGE VIA FLASK (INDEX.HTML) ------------------------------#
@app.route('/')
def home():
    return render_template('index.html')

#------------------------ RENDER YOUTUBE PAGE (YOUTUBE.HTML) ------------------------------#
@app.route('/youtube', methods=['GET', 'POST'])
def youtube_searcher():
    form = SearchForm()
    custom_label = "Enter Video URL"
    search_performed = False
    error_message = None
    video_data = None

    if form.validate_on_submit():
        search_performed = True
        youtube_url = form.post_url.data

        try:
            video_id = get_video_id(youtube_url)  # Extract video ID
            if not video_id:
                raise ValueError("Invalid YouTube URL. Could not extract video ID.")

            print(f"Extracted video ID: {video_id}")
            video_data = get_youtube_details(YOUTUBE_API_KEY, video_id)  # Fetch video details

            if not isinstance(video_data, dict):  # Validate video data structure
                raise ValueError("Invalid video data received. Please check the YouTube URL.")

        except Exception as e:
            error_message = f"Error: {str(e)}"
            video_data = None  # Reset video_data to prevent further processing

        # Render stats and placeholder for sentiment summary
        return render_template(
            'analysis.html',
            title=video_data.get('title') if video_data else None,
            description=video_data.get('description') if video_data else None,
            thumbnail=video_data.get('thumbnail') if video_data else None,
            post_date=video_data.get('post_date') if video_data else None,
            view_count=video_data.get('view_count') if video_data else None,
            like_count=video_data.get('like_count') if video_data else None,
            comment_count=video_data.get('comment_count') if video_data else None,
            youtube_url=youtube_url,  # Pass youtube_url to be rendered in HTML
            platform="youtube",
            search_performed=search_performed,
            error_message=error_message
        )

    return render_template(
        'youtube.html',
        form=form,
        custom_label=custom_label,
        search_performed=search_performed,
        error_message=error_message
    )

#------------------------ ANALYSIS ROUTE FOR YOUTUBE -------------------------#
@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    youtube_url = request.form.get('youtube_url')  # Extract youtube_url from URL-encoded form data
    if not youtube_url:
        return {"error": "YouTube URL not provided."}, 400

    video_id = get_video_id(youtube_url)  # Extract video ID
    print(f"Video ID for sentiment analysis: {video_id}")

    comments = get_video_comments(YOUTUBE_API_KEY, video_id)
    if comments:
        summarizer = SentimentSummarizer()
        try:
            sentiments, num_positive, num_negative = summarizer.analyze_comments(comments)
            summary = summarizer.generate_user_friendly_summary(sentiments, num_positive, num_negative)
            return {"summary": summary}, 200
        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            return {"error": "An error occurred during sentiment analysis. Please try a different video."}, 500
    else:
        return {"error": "No comments found for this video or an error occurred."}, 400


# # #------------------------RENDER REDDIT PAGE (REDDIT.HTML)------------------------------#

@app.route('/reddit', methods=['GET', 'POST'])
def reddit_searcher():
    form = SearchForm()
    custom_label = "Enter Post URL"
    search_performed = False
    error_message = None
    post_data = None
    reddit_url = None

    if form.validate_on_submit():
        search_performed = True
        reddit_post_url = form.post_url.data
        reddit_url = reddit_post_url
        reddit_post_id = extract_post_id(reddit_post_url)
        print(f"Reddit Post URL: {reddit_url}")  # Debugging
        print(f"Reddit Post ID: {reddit_post_id}")  # Debugging

        reddit_api = RedditAPI()
        post_data = reddit_api.get_reddit_comments_and_info(reddit_post_id)
        print(f"Post Data: {post_data}")  # Debugging

        if post_data is None or post_data == "Post not found":
            error_message = "The post could not be found. Please check the URL and try again."
            post_data = None



        # Check if the request is an AJAX request using FLASK 'request' object
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return only the relevant HTML for reviews
            return render_template(
                'analysis.html',
                title=post_data['title'] if post_data else None,
                comment_count=post_data['comment_count'] if post_data else None,
                upvotes=post_data['upvotes'] if post_data else None,
                downvotes=post_data['downvotes'] if post_data else None,
                post_date=post_data['post_date'] if post_data else None,
                subreddit=post_data['subreddit'] if post_data else None,
                subreddit_members=post_data['subreddit_members'] if post_data else None,
                comments=post_data['comments'] if post_data else None,
                platform="reddit" if post_data else None,
                score="score" if post_data else None,
                search_performed=search_performed,
                error_message=error_message,
                reddit_url=reddit_url





            )



    # Default rendering for GET requests
    return render_template('reddit.html', form=form, custom_label=custom_label, search_performed=search_performed, error_message=error_message)



#--------------------- ANALYSIS ROUTE FOR REDDIT ---------------------------#

@app.route('/analyze_reddit_sentiment', methods=['POST'])
def analyze_reddit_sentiment():
    reddit_url = request.form.get('reddit_url')  # Extract reddit_url from URL-encoded form data
    print(f"Reddit URL Received: {reddit_url}")  # Debugging
    if not reddit_url:
        return {"error": "Reddit URL not provided."}, 400

    try:
        reddit_post_id = extract_post_id(reddit_url)
        reddit_api = RedditAPI()
        post_data = reddit_api.get_reddit_comments_and_info(reddit_post_id)
        comments = post_data.get('comments', [])

        if comments:
            summarizer = SentimentSummarizer()
            sentiments, num_positive, num_negative = summarizer.analyze_comments(comments)
            summary = summarizer.generate_user_friendly_summary(sentiments, num_positive, num_negative)
            return {"summary": summary}, 200
        else:
            return {"error": "No comments found for this post or an error occurred."}, 400
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return {"error": "An error occurred during sentiment analysis. Please try again."}, 500


#------------------------ RENDER TIKTOK PAGE (TIKTOK.HTML) ------------------------------#

@app.route('/tiktok', methods=['GET', 'POST'])
def tiktok_searcher():
    form = SearchForm()
    custom_label = "Enter Video URL"
    return render_template('tiktok.html', form=form, custom_label=custom_label)




#------------------------ CONTACT FORM SETUP VIA FLASKFORM------------------------------#


class ContactForm(FlaskForm):
    name = StringField(
        "Your Name",
        validators=[
            DataRequired(message="Name is required."),
            length(max=100, message="Name must be less than 100 characters.")
        ],
        render_kw={"placeholder": "Enter your name", "class": "form-control", "id": "userName"}
    )
    email = StringField(
        "Your Email",
        validators=[
            DataRequired(message="Email is required."),
            email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "Enter your email", "class": "form-control", "id": "userEmail"}
    )
    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(message="Message is required."),
            length(max=1000, message="Message must be less than 1000 characters.")
        ],
        render_kw={
            "placeholder": "Describe the error or your message here",
            "class": "form-control",
            "id": "userMessage",
            "rows": 5
        }
    )
    submit = SubmitField("Send Message", render_kw={"class": "btn btn-primary d-grid"})

#---------------------------- RENDER CONTACT PAGE (CONTACT.HTML) ----------------------------#
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Debugging
        print(f"Name: {name}, Email: {email}, Message: {message}")

        # Create email message
        msg = Message(
            subject="VibeCheckr Contact Form Submission",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n {message}"

        )
        # Debugging: Print to console
        print(f"Attempting to send email...\nFrom: {app.config['MAIL_DEFAULT_SENDER']}\nTo: recipient_email@gmail.com\nMessage: {message}")

        # Send the email
        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")  # Print error to console
            flash(f"Failed to send message: {e}", "danger")

        return redirect(url_for('contact'))

    print("Form validation failed.")  # If form validation fails
    return render_template('contact.html', form=form)













if __name__ == '__main__':
    app.run(debug=True)



