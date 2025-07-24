/* Import font */
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

/* Overall style */
body, .stApp {
    background-color: #003300;
    font-family: 'Quicksand', sans-serif;
    color: white;
    transition: background-color 1s ease;
}

/* Headings */
h1, h2, h3 {
    font-weight: 600;
    color: #fdd;
}

/* Paragraph and text */
p, label, .css-10trblm {
    color: #eee;
    font-size: 1.05em;
}

/* Chat bubbles */
.momly-bubble {
    background-color: #ffe6f0;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 6px 0;
    max-width: 80%;
    display: inline-block;
    animation: fadeIn 0.5s ease-in;
}

.user-bubble {
    background-color: #d9fdd3;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 6px 0;
    max-width: 80%;
    display: inline-block;
    float: right;
    animation: fadeIn 0.5s ease-in;
}

/* Fade-in animation */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

/* Buttons */
button, .stButton > button {
    background-color: #c94f7c !important;
    color: white !important;
    border-radius: 10px !important;
}

/* --- Styles for MOMLY character (now more like a logo) --- */
.momly-character {
    position: fixed; /* Fixes the position relative to the viewport */
    top: 20px;       /* Position from the top */
    left: 20px;      /* Position from the left */
    width: 100px;    /* Smaller, logo-like size */
    height: auto;
    z-index: 1001;   /* Ensure it's above other elements, including sidebar */
    pointer-events: none; /* Allows clicks to pass through */
}

/* Optional: Media query for smaller screens to hide or resize */
@media (max-width: 768px) {
    .momly-character {
        width: 80px; /* Even smaller on mobile */
        top: 10px;
        left: 10px;
    }
}
/* --- End of MOMLY character styles --- */


/* --- New styles for moving Streamlit sidebar to the right --- */
/* Target the sidebar container */
section.main .block-container {
    padding-right: 250px; /* Add padding to the right to make space for the sidebar */
    padding-left: 1rem; /* Keep existing left padding or adjust */
}

/* Target the sidebar itself */
section[data-testid="stSidebar"] {
    position: fixed; /* Keep it fixed */
    top: 0;
    right: 0;        /* Move to the right */
    left: auto;      /* Remove left positioning */
    width: 250px;    /* Standard sidebar width, adjust if needed */
    height: 100vh;   /* Full height */
    z-index: 999;    /* Ensure it's above main content but below the character logo if character is on top */
    background-color: #1a1a1a; /* Darker background for sidebar, adjust as per your theme */
    padding-top: 20px; /* Add padding for content inside sidebar */
    border-left: 1px solid #c94f7c; /* Optional: add a subtle border */
}

/* Adjust the sidebar collapse button if needed */
button[data-testid="stSidebarCollapseButton"] {
    right: 250px; /* Adjust its position to stay on the left of the moved sidebar */
    left: auto;
}

/* This targets the main content area */
.main {
    margin-left: 0; /* Remove default left margin */
    margin-right: 250px; /* Add margin on the right to accommodate sidebar */
}

/* Ensure the character doesn't overlap with main content too much */
.block-container {
    padding-top: 1rem;
}
/* --- End of new sidebar styles --- */
