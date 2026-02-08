import fetch from 'node-fetch';

const apiKey = process.env.GOOGLE_API_KEY || 'YOUR_API_KEY';
const url = `https://generativelanguage.googleapis.com/v1/models?key=${apiKey}`;

async function listModels() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log(JSON.stringify(data, null, 2));
    } catch (error) {
        console.error('Error:', error);
    }
}

listModels();
