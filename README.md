# TodoApp Dashboard Redesign

This README describes the responsive redesign of the TodoApp dashboard, focusing on the task card layout and overall page responsiveness.

## Goal
Convert the current square task cards into a clean, vertical feed where each task card spans the available content width. The layout is visually polished on desktop (centered, max width ~900px) and fully responsive on tablets and phones. The UI/UX is friendly for touch devices, with accessible touch targets and no horizontal overflow or white gaps.

## Implementation Details

### Layout
- The main page content is centered horizontally with a `max-width` of approximately 900px. This is achieved by setting `max-w-3xl` and `mx-auto` on the `<main>` tag in `templates/base.html`.
- Task cards are now a full-width vertical list within this container, achieved using Tailwind CSS flexbox utilities in `templates/dashboard.html` and custom CSS in `static/style.css`.

### Card Style
- **Rounded Corners:** `border-radius: 12px` is applied using `rounded-xl` Tailwind class on `.task-card`.
- **Soft Shadow:** `box-shadow: 0 4px 12px rgba(0,0,0,0.06)` is applied using `shadow-md` Tailwind class on `.task-card`.
- **Internal Padding:** `padding: 18px` is applied using `p-4` Tailwind class on `.task-card`.
- **Hierarchy:**
    - Title is on top (bold, `text-lg font-bold`).
    - Status badge is near the title (`status-badge` class).
    - Description is below the title/badge (`text-sm text-gray-600`).
    - Meta row with date and action buttons is aligned to the right on desktop/tablet, and stacked on mobile.

### Responsiveness

The design uses Tailwind CSS's responsive breakpoints, primarily `sm` (640px) for tablet-like adjustments and custom media queries for finer control.

- **Desktop (≥ 992px):**
    - Centered container with `max-width: 900px`.
    - Card width equals container width.
    - Buttons and badges are inline to the right of their respective content.

- **Tablet (≥ 768px and < 992px):**
    - Similar to desktop, but Tailwind's `sm:` breakpoint handles minor adjustments.
    - Icons and spacing adapt naturally with Tailwind's utility classes.

- **Mobile (< 768px):**
    - Achieved using a custom media query `@media (max-width: 767px)` in `static/style.css`.
    - **Stacked Controls:** Status badges remain next to the title. Action buttons collapse into a full-width row under the description, distributed using `justify-around`.
    - **Button Touch Targets:** Action buttons (`.action-button`) have a `min-width: 44px` and `min-height: 44px` to ensure accessible touch targets.

### Header/Controls
- The "Add New Task" button and filter tabs (if present on the `home` page, not directly on `dashboard.html`) are expected to adapt. On `dashboard.html`, the "View All Tasks" button remains visible and adapts with Tailwind's responsive classes.

### Accessibility & UX
- Keyboard navigability and visible focus styles are inherent to Tailwind's default styling for interactive elements.
- Sufficient color contrast is maintained through the chosen Tailwind color palette.
- Smooth vertical scrolling is ensured by avoiding horizontal overflow.

## Files Updated
- `templates/base.html`: Adjusted `<main>` tag classes for max-width and centering.
- `templates/dashboard.html`: Restructured "Recent Tasks" section HTML for new card layout.
- `static/style.css`: Added new CSS for `.task-card`, `.status-badge`, `.action-button` and mobile-specific media queries.

## To View Changes
1. Ensure the Flask application is running.
2. Navigate to the dashboard page.
3. Resize your browser window or use developer tools to inspect responsiveness at different breakpoints.
