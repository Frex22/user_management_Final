{% include 'header.md' %}

# Professional Status Update

Dear {{ name }},

We're pleased to inform you that your account has been {% if is_professional %}upgraded to professional status{% else %}updated from professional status{% endif %}.

{% if is_professional %}
As a professional user, you now have access to:
- Enhanced profile visibility
- Additional networking features
- Professional community access
- Advanced search capabilities

We encourage you to update your profile to showcase your professional experience and skills.
{% else %}
Your account has been updated to reflect your current status. If you believe this change was made in error, please contact our support team.
{% endif %}

Thank you for being a valued member of our platform.

Best regards,
The User Management Team

{% include 'footer.md' %}