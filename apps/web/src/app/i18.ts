// src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
// فایل‌های ترجمه خود را import کنید
// import translationEN from './locales/en/translation.json';
// import translationFA from './locales/fa/translation.json';

i18n
    .use(initReactI18next)
    .init({
        // resources,
        lng: 'fa', // زبان اولیه
        fallbackLng: 'fa',
        interpolation: {
            escapeValue: false,
        },
    });

export default i18n;
