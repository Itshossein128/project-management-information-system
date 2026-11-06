# راهنمای مدیر / Manager guide

This guide uses the screens a manager sees. It does not contain a password, a recovery link, or a session secret. The access token from sign-in lasts one hour. After sign-out, that session is not refreshed. If sending is not configured, the product says no message was sent.

## ساخت حساب یا عضویت / Create an account or membership

1. Sign in. Persian: «شماره تلفن»، «رمز عبور»، «ورود». English: “Phone number”, “Password”, “Sign in”.
2. An organization account administrator opens the people administration screen and creates a normal person, or the project manager selects a person who already exists.
3. Open the project, then Settings, then Members. Persian button: «افزودن عضو». English: “Add member”.
4. Search, choose the person, choose one or more roles, and save. Persian: «جستجو»، «نقش‌ها»، «ذخیره». English: “Search”, “Roles”, “Save”.
5. Saving the same person again must not create a second account or a second membership.

## تخصیص نقش و استثنا / Assign a role or an exception

1. On Members, choose «ویرایش» / “Edit” for that person.
2. Role checkboxes apply only in this project. A role created for another project is not offered here. Organization role settings are a different screen from this project's roles.
3. Open «دسترسی‌های پیشرفته» / “Advanced permissions”.
4. Each permission has three choices: «ارث» / “Inherit”, «اعطا» / “Grant”, and «رد» / “Deny”. The choice is named with the permission, so a screen reader can tell them apart.
5. Two roles add together. Deny overrides that sum. A direct request to finish an action after Deny is refused.
6. Choose Inherit again. The form shows the role's own result, and the message is «تنظیم دستی حذف شد» / “Override cleared”.

## لغو دسترسی و تاریخچه / Revoke access and read history

1. On the member row, the status control is «وضعیت» / “Status”. Choose «غیرفعال» / “Inactive”.
2. That person no longer opens this project's data. Documents they already recorded stay, with their name.
3. Open «تاریخچه کامل دسترسی» / “Full access history”. The heading is «تاریخچه دسترسی» / “Access history”.
4. The row shows the person, the actor, the project, the time, and the values before and after. A password or token is not shown.

## بازیابی ورود / Recover sign-in

1. Sign out. Refreshing the old session is refused.
2. Recovery is available only when a real send channel and an agreed test recipient exist. Otherwise the screen says the message was not sent. Do not treat that as a delivered recovery link.
3. A recovery link that has already been used does not work again. That live delivery was not run for this package, so recovery is not marked passed.

## آنچه این راهنما انجام نمی‌دهد / What this guide does not do

The customer has not signed. The customer environment and the acceptor are not named. File storage did not answer, and no message was sent.
