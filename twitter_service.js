import { Scraper } from 'agent-twitter-client';
import express from 'express';
import dotenv from 'dotenv';
import fs from 'fs';
dotenv.config();

const app = express();
let scraper = null;

// Initialize scraper with cookie handling
async function initScraper() {
    try {
        console.log("Initializing scraper")
        if (scraper && await scraper?.isLoggedIn()) {
            console.log("Scraper already initialized")
            return true;
        }
        scraper = new Scraper();
        // const existingCookies = await scraper.getCookies()
        // read cookies from file
        const existingCookies = JSON.parse(fs.readFileSync('cookies.json', 'utf8'));
        if (existingCookies && existingCookies.length > 0) {
            console.log("Using existing cookies")
        } else {
            console.log(process.env.TWITTER_USERNAME);
            // First try to login
            await scraper.login(
                process.env.TWITTER_USERNAME,
                process.env.TWITTER_PASSWORD,
                process.env.TWITTER_EMAIL
            );
        }

        // Get and cache cookies after successful login
        const cookies = await scraper.getCookies();
        // save cookies to file
        fs.writeFileSync('cookies.json', JSON.stringify(cookies, null, 2));
        console.log('Got cookies:', cookies);
        
        // Store cookies for future use
        if (cookies) {
            await scraper.setCookies(cookies);
        }

        console.log('Successfully logged into Twitter');
        return true;
    } catch (error) {
        console.error('Failed to initialize scraper:', error);
        return false;
    }
}

async function getTweets(username) {
    // if tweets file exists, read from file
    if (fs.existsSync(`tweets-${username}.json`)) {
        const tweets = JSON.parse(fs.readFileSync(`tweets-${username}.json`, 'utf8'));
        console.log(`total tweets for ${username}: ${tweets.length}`)
        return tweets;
    }
    return null;
}
// Routes
app.get('/tweets/:username/:count', async (req, res) => {
    const tweets = await getTweets(req.params.username);
    if (tweets) {
        console.log('Using cached tweets')
        res.json(tweets);
        return;
    }
    try {
        if (!scraper || !(await scraper.isLoggedIn())) {
            const success = await initScraper();
            if (!success) {
                throw new Error('Failed to initialize Twitter scraper');
            }
        }

        console.log(req.params.username, req.params.count)
        // Get tweets using async iterator
        const tweets = [];
        const tweetIterator = scraper.getTweets(req.params.username, req.params.count);
        
        for await (const tweet of tweetIterator) {
            tweets.push(tweet);
        }
        console.log(`total tweets for ${req.params.username}: ${tweets.length}`)
        // save tweets to file
        fs.writeFileSync(`tweets-${req.params.username}.json`, JSON.stringify(tweets, null, 2));
        res.json(tweets);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/trends', async (req, res) => {
    try {
        if (!scraper || !(await scraper.isLoggedIn())) {
            const success = await initScraper();
            if (!success) {
                throw new Error('Failed to initialize Twitter scraper');
            }
        }
        const trends = await scraper.getTrends();
        res.json(trends);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Twitter service running on port ${PORT}`);
});