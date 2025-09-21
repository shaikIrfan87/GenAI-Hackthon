# 📧 Email Configuration Setup Guide

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Security → 2-Step Verification
3. Turn on 2-Step Verification

### Step 2: Generate App Password
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Select "Mail" and your device
4. Copy the generated 16-character password

### Step 3: Update .env File
Replace the placeholder values in your `.env` file:

```env
# Email Configuration for Gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_actual_email@gmail.com
MAIL_PASSWORD=your_16_character_app_password
MAIL_DEFAULT_SENDER=your_actual_email@gmail.com
```

### Example .env Configuration:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=recruiter@company.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=recruiter@company.com
```

## Other Email Providers

### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
```

### Yahoo Mail
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_email@yahoo.com
MAIL_PASSWORD=your_app_password
```

## Testing Email Configuration

1. Update your `.env` file with correct credentials
2. Restart the application
3. Check console output for: "📧 Email service initialized with: your_email@gmail.com"
4. Try sending a test email from the Cover Letter page

## Troubleshooting

### "Username and Password not accepted" Error
- Make sure you're using an App Password, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled on your Google account
- Double-check the email address and app password

### "Authentication failed" Error
- Verify the email credentials are correct
- For Gmail, ensure "Less secure app access" is disabled (use App Password instead)
- Check if your email provider requires specific SMTP settings

### Firewall/Network Issues
- Ensure port 587 (TLS) or 465 (SSL) is not blocked
- Try different SMTP ports if needed

## Security Notes
- Never commit real email credentials to version control
- Use App Passwords instead of regular passwords
- Keep your `.env` file secure and out of public repositories