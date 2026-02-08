
def get_email_template(name, email, subject, message, company_name, company_logo, company_website):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{company_name}</title>
</head>
<body style="margin:0; padding:0; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height:1.6;">
  <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
    <tr>
      <td style="padding:0;">
        <!--[if mso]>
        <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:100%;height:auto;">
          <v:fill color="#121c2d" />
          <v:textbox inset="0,0,0,0">
        <![endif]-->
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="width:100%; max-width:100%; min-width:100%; margin:0; border-radius:20px; border:1px solid rgba(255,255,255,0.08); overflow:hidden; background-color:#0f172a; box-shadow: 0 30px 60px rgba(12, 20, 40, 0.6), 0 0 60px rgba(12, 20, 40, 0.25);">
          <tr>
            <td style="padding:24px 0 12px; text-align:center;">
              <img src="cid:company_logo" alt="{company_name} logo" width="120" style="display:inline-block; width:120px; height:auto; border:0; outline:none; text-decoration:none;">
              <div style="height:16px;"></div>
              <h1 style="margin:0; font-size:20px; font-weight:700; letter-spacing:0.2px; color:#e5e7eb;">
                {subject}
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 12px; text-align:center;">
              <p style="margin:0; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:2px; color:#94a3b8;">
                Message
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 24px;">
              <div style="background-color:#131a2b; border:1px solid rgba(255,255,255,0.06); border-radius:16px; padding:24px 36px; box-shadow: inset 0 0 0 1px rgba(6, 182, 212, 0.08);">
                <p style="margin:0; font-size:16px; color:#cbd5e1; line-height:1.8; white-space:pre-wrap;">
{message}
                </p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 24px; text-align:center;">
              <a href="{company_website}" style="display:inline-block; background-color:#0e7490; color:#ffffff; text-decoration:none; padding:14px 28px; border-radius:10px; font-size:15px; font-weight:700; letter-spacing:0.2px; box-shadow: 0 12px 24px rgba(14, 116, 144, 0.35); border:1px solid rgba(255,255,255,0.12);">
                Visit Our Website
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding:0;">
              <div style="height:20px;"></div>
            </td>
          </tr>
        </table>
        <!--[if mso]>
          </v:textbox>
        </v:rect>
        <![endif]-->
      </td>
    </tr>
  </table>
</body>
</html>
"""
