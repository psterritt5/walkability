import * as React from 'react';
import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';

const config = require('../config.json');

export default function HomePage() {
    const [gpsCoordinates, setGpsCoordinates] = useState('');
    const [walkabilityScore, setWalkabilityScore] = useState(null);
    const [errorMessage, setErrorMessage] = useState(''); // use when invalid coordinates are entered

    const handleInputChange = (event) => {
        setGpsCoordinates(event.target.value);
    };

    const fetchWalkabilityScore = async () => {
        try {
            const response = await fetch(`http://${config.server_host}:${config.server_port}/result`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ coordinates: gpsCoordinates }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch walkability score. Please try again.');
            }

            const data = await response.json();
            setWalkabilityScore(data.result);
            setErrorMessage('');
        } catch (error) {
            setErrorMessage(error.message);
            setWalkabilityScore(null);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); 
            if (gpsCoordinates) {
                fetchWalkabilityScore();
            }
        }
    };

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
                textAlign: 'center',
            }}
        >
            <Box sx={{ mb: 2 }}>
                <h2>Welcome to Walkability Navigator</h2>
                <p>Enter GPS coordinates below to check your new home's walkability!</p>
            </Box>

            <Box
                component="form"
                sx={{ '& > :not(style)': { m: 1, width: '50ch' } }}
                noValidate
                autoComplete="off"
            >
                <TextField
                    id="outlined-basic"
                    label="Enter GPS coordinates"
                    variant="outlined"
                    value={gpsCoordinates}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyPress}
                />
            </Box>

            <Box sx={{ mt: 2 }}>
                <Button 
                    variant="contained" 
                    onClick={fetchWalkabilityScore} 
                    disabled={!gpsCoordinates}
                >
                    Check Walkability
                </Button>
            </Box>

            <Box sx={{ mt: 2 }}>
                {walkabilityScore !== null && (
                    <p><strong>Walkability Score:</strong> {walkabilityScore}</p>
                )}
                {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
            </Box>

            <Box sx={{ mt: 2 }}>
                <img 
                    src="https://images.adsttc.com/media/images/5ffe/8b53/63c0/174c/f800/00f1/newsletter/paris_en_commun.jpg?1610517326" 
                    alt="Image of walkable city" 
                    style={{ maxWidth: '100%', height: 'auto' }}
                />
            </Box>
        </Box>
    );
}
