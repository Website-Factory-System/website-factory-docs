# Client IP in Namecheap API

## What is Client IP?

The Client IP is a security feature required by Namecheap's API. It's the IP address from which API requests will be made to Namecheap. This acts as an additional layer of security to ensure that only authorized servers can make changes to your domains.

## How it works

1. **Single Server Setup**: If you're using one server, that server's IP address should be set as the Client IP.

2. **Multiple Servers**: In the Website Factory system, since all API calls to Namecheap are made from the Management Hub API (running on Railway or your deployment server), you should use:
   - The IP address of your Railway deployment
   - OR the IP address of the server where the Management Hub API is hosted

## Important Notes

- The Client IP must be whitelisted in your Namecheap account settings
- You can find this setting in Namecheap under Profile > Tools > API Access
- The IP must match exactly - Namecheap will reject API calls from non-whitelisted IPs
- For development, you might need to add your local machine's public IP

## In the Settings Page

The Client IP field now shows a dropdown of your configured servers. This makes it easy to select the appropriate server IP without having to remember or copy/paste IP addresses.

If you're using Railway for the Management Hub API, you'll need to:
1. Find Railway's outbound IP address
2. Add that IP to Namecheap's whitelist
3. Either create a server entry for Railway or manually enter the IP

## Security Best Practice

Only whitelist IPs that absolutely need access to the Namecheap API. Remove any IPs that are no longer in use to maintain security.