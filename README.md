# Whatsminer Integration for Home Assistant

**Description**: Elevate your Home Assistant experience by integrating it with Whatsminer devices. This plugin leverages the Whatsminer API to fetch and display crucial mining statistics and device health information.

Tested with Home Assistant version `2023.10.4`.

## Supported Whatsminer API Versions
- `V1.4.0`
- `V2.0.X`

## Compatibility List
- `M20S` - API Version: `1.4.0`
- `M30S/+/++` - API Version: `2.0.5`
- `M31S/+` - API Version: `2.0.5`
- `M50S/+/++` - API Version: `2.0.5`

## Key Features
- **Mining Overview**: Real-time insights into your mining performance.
- **Health Monitoring**: Stay informed about the operational status of your Whatsminer devices.
- **Easy Integration**: Configure the integration using either Home Assistant's UI or YAML.

## Installation

### Via Home Assistant UI
1. Open the HACS section in Home Assistant.
2. Access the menu (top right corner) and choose `Custom repositories`.
3. Input the GitHub repository URL for this integration, label it, then click `Add`.
4. After adding, proceed as follows:

   - Head to `Configuration` > `Integrations`.
   - Opt for `Add Integration` and pick `Whatsminer API`.
   - During the setup process, provide the miner's host, port (default: `4028`), and password (default: `admin`).
   - Confirm that your device has the WhatsMiner API activated. Activate it using the WhatsMinerTool if needed.

## Troubleshooting

Experiencing issues? Try the following:

- Consult the [Whatsminer API V2.0.5 manual](https://aws-microbt-com-bucket.s3.us-west-2.amazonaws.com/WhatsminerAPI%20V2.0.5.pdf) for comprehensive guidelines and troubleshooting tips.
- Double-check that the WhatsMiner API is active on your device. Use the WhatsMinerTool for this purpose.
- Verify the accuracy of the host, port, and password you provided during the setup.

## Get Involved

Your contributions can make a difference! Feel free to [propose changes or enhancements](#) or simply share your feedback.

## Credits

- **Founding Developer**: [incaseoftrouble](https://github.com/incaseoftrouble/whatsminer-homeassistant)
- **Updates for HA 2023.05.03**: [DanyaSWorlD](https://github.com/DanyaSWorlD/whatsminer-homeassistant)

Special thanks to the developers and the community for their invaluable contributions.