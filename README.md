# Scraping Free Games AWS

This project is a web application that fetches free games from the Epic Games Store and displays them to users. It consists of a frontend built with HTML, CSS, and JavaScript, and a backend AWS Lambda function that handles API requests.

## Features

- User-friendly interface to discover free games
- Email validation before accessing results
- Dynamic display of game information including title, description, prices, and availability dates
- Responsive design
- AWS Lambda backend to handle CORS and API requests

## Project Structure

- `index.html`: Main landing page with email form
- `results.html`: Page displaying the fetched games
- `script.js`: JavaScript for form validation and API calls
- `styles.css`: CSS styles for the application
- `assets/`: Directory for static assets like background images
- `aws/lambda_function.py`: AWS Lambda function for fetching Epic Games Store data

## Setup

### Frontend

1. Open `index.html` in a web browser or serve the files using a local server.

### Backend (AWS Lambda)

**Why Lambda is Required:**
The Epic Games Store API doesn't allow direct CORS requests from browsers. The Lambda function acts as a proxy, fetching data from the API and returning it with proper CORS headers.

**Setup Steps:**

1. **Deploy Lambda Function:**
   - Go to AWS Lambda Console
   - Create a new function (Python 3.12 runtime)
   - Copy the code from `aws/lambda_function.py`
   - Configure:
     - Memory: 128 MB
     - Timeout: 10 seconds
     - No layers needed (uses only stdlib)

2. **Create Function URL:**
    - In Lambda configuration, create a Function URL
    - Auth type: NONE (public access)
    - Configure CORS:
      - Allow origins: *
      - Allow methods: GET, OPTIONS
      - Allow headers: Content-Type
    - Copy the generated URL (e.g., `https://abc123.lambda-url.us-east-1.on.aws/`)

3. **Update Frontend:**
   - Open `script.js`
   - Replace `'YOUR_LAMBDA_URL_HERE'` with your Lambda Function URL

## Lambda Function Response

The Lambda function returns JSON data in this format:

```json
{
  "scraped_at": "2025-11-17T15:26:53.923642",
  "total_games": 3,
  "games": [
    {
      "title": "Game Title",
      "description": "Game description",
      "slug": "game-slug",
      "url": "https://store.epicgames.com/...",
      "original_price": "R$ XX,XX",
      "discount_price": "Grátis",
      "publisher": "Publisher Name",
      "developer": "Developer Name",
      "discount_percentage": 100,
      "banner": "banner-url",
      "thumbnail": "thumbnail-url",
      "start_date": "2025-11-13T16:00:00.000Z",
      "end_date": "2025-11-20T16:00:00.000Z",
      "end_date_formatted": "20/11/2025 às 13:00"
    }
  ],
  "source": "Epic Games Store API",
  "locale": "pt-BR"
}
```

## Deployment

### Frontend Deployment

Host the static files (HTML, CSS, JS, assets) on any static hosting service:

- **AWS S3 + CloudFront**: Recommended for AWS integration
  - Create S3 bucket with static website hosting
  - Upload frontend files
  - Configure CloudFront for CDN
  
- **GitHub Pages**: Free hosting for public repositories
- **Netlify**: Easy deployment with continuous integration
- **Vercel**: Fast static site hosting

### Backend Deployment

The Lambda function is already deployed in AWS. Just ensure:
- Function URL is public
- CORS headers are properly configured (already in code)
- Function has appropriate timeout (10 seconds recommended)

## Cost Estimation

- **Lambda**: FREE TIER (1M requests/month free)
  - ~1 second per execution
  - 128MB memory sufficient
  - Estimated: $0.00/month for typical usage

- **S3 + CloudFront**: FREE TIER available
  - 5GB storage free
  - 50GB transfer free/month

## Technologies Used

- HTML5
- CSS3
- JavaScript (ES6+)
- AWS Lambda
- Python 3.12 (for Lambda function)
- Epic Games Store API

## Author

Jonathas Rocha De Souza

## License

This project is for educational purposes. Please respect Epic Games' terms of service when using their API.