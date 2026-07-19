## 2026-07-16 - Explicit Focus States for Keyboard Parity
**Learning:** Raw HTML buttons (like the NotificationBell) and custom components (like segmented-control) in this app often lack the global focus-visible outlines that standard design system components receive. This creates keyboard accessibility dead zones.
**Action:** Always manually apply the global focus ring utilities (`outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]`) to custom interactive elements to ensure visual parity for keyboard users.

## 2024-05-14 - Accessible Loading States
**Learning:** Adding aria-busy={true} along with a loading spinner greatly improves accessibility during async form submissions by notifying screen readers of the waiting state. Additionally, `inline-flex items-center gap-2` is an effective pattern for seamlessly aligning the spinner and text within buttons.
**Action:** When implementing loading states for async actions on buttons, always include `aria-busy={true}` and a visual spinner with flex alignment.
