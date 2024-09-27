# HACS Honeygain
The Honeygain integration lets you access account balances and daily earnings from [Honeygain](https://r.honeygain.me/LEWISF7B55).

Honeygain is a platform where you can sell your idle bandwidth to make a bit of extra cash. This integration will let you keep an eye on your account balances.

## Prerequisites
You must have a Honeygain account. Sign up [here](https://r.honeygain.me/LEWISF7B55) to get free credits.

## Setup
This integration uses a config flow to collect credentials

- Email Address: Your Honeygain account's email address, this is required.
- Password: Your Honeygain password for the account, this is required.

## Entities

### Sensor
The integration will create sensor entities for metrics that relate to your account:

- Account balance
- Today's current earnings
- Number of active devices

### Button
The integration exposes a button for automating tasks:

- Opening the daily pot

## Example Config
#### Example 1: Automate opening the Lucky Pot at 11pm each day, if we've earned the minimum
```yaml
- id: '<generated>'
  alias: Open Lucky Pot
  description: Check when we are able to open the Honeygain Lucky Pot, and open it
  trigger:
  - platform: time_pattern
    hours: '23'
    minutes: '0'
    seconds: '0'
  condition:
  - condition: numeric_state
    entity_id: sensor.today_s_earnings
    above: 0.015
  action:
  - service: button.press
    data: {}
    target:
      entity_id: button.open_lucky_pot
  mode: single
  ```