<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.0/css/all.min.css">

<style>
    #input-container {
        position: fixed;
        bottom: 0;
        width: 100%;
        padding: 12px;
        background-color: white;
        box-shadow: 0 -3px 10px rgba(0, 0, 0, 0.1);
        z-index: 100;
    }

    h1, h2 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 3em;
        background: linear-gradient(90deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2);
        padding: 15px 20px;
        display: inline-block;
        background-color: rgba(241, 6, 6, 0.2); /* Light grey faded background */
        border-radius: 8px; /* Slightly rounded edges for a modern look */
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    }

    .user-avatar, .bot-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
    }

    .user-avatar {
        float: right;
        margin-left: 8px;
        margin-bottom: -12px;
    }

    .bot-avatar {
        float: left;
        margin-right: 8px;
    }
</style>
