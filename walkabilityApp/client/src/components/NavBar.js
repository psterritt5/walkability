import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

export default function ButtonAppBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Walkability Navigator  
                <Button color="inherit" href="/">Home</Button>
                <Button color="inherit" href="/dashboard">Dashboard</Button>
            </Typography>
            <Button color="inherit" href="/login">Login</Button>
            <Button color="inherit" href="/register">Register</Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}


/*export default function NavBar(){
    return(
        <nav class="navbar">
            <div class="navbar-brand">Walkability Navigator</div>
            <div class="navbar-container">
                <ul class="navbar-list">
                    <li> <a aria-current="page" href="/">Home</a> </li>
                    <li> <a href="/dashboard">Dashboard</a> </li>
                        <li > <a href="/login">Login</a> </li>
                        <li> <a href="/register">Register</a> </li>
                </ul>
                <span class="navbar-text">
                Let us help you find your new home!
                </span>
            </div>
        </nav>
    );
}*/