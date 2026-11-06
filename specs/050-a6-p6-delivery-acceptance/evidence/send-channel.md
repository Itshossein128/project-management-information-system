# Live send channel

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

`send_channel`: `not_configured`

`EMAIL_BACKEND` and `SMS_PROVIDER` are unset, so delivery uses the console email backend and the console SMS provider. `TEAM_DELIVERY_TEST_RECIPIENT` is unset. `notifications.services.delivery.email_is_operational` and `sms_is_operational` are therefore false, and `deliver_account_message` returns `not_configured` or `not_sent`. No message was sent.

The secure account path remains the tested equivalent. This note must not be read as a sent invitation or recovery message.
