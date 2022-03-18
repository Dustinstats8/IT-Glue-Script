# IT Glue Groups #

Vision
-------
At the time this script was developed, IT Glue did not have the ability to bulk add configurations to security groups. To resolve this, an API call is made that
pulls all configuration URLs and then uses Selenium to automate moving them to the IT security group. This script will live on the same server as the Nexus 
for ease of use.
<hr>

Please note: While Selenium is controlling the web browser, the machine it's running on is effectively unusable because if the focus is taken off of the Selenium
browser, the script will break.
