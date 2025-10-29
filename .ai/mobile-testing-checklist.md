# Mobile Responsiveness Testing Checklist

## Quick Test Protocol

### 🔍 Chrome DevTools Device Emulation

#### iPhone SE (375px) - Smallest Device
```
- [ ] State 1: Coffee machine scales correctly, no horizontal scroll
- [ ] State 2: Columns stack vertically (3 boxes, one above the other)
- [ ] State 3: Grid shows 1 column only
- [ ] State 4: Hamburger menu button visible top-left
- [ ] State 4: Swipe left/right navigates between sparks
- [ ] Action bar: Buttons stack vertically, full width
- [ ] Icon navigation: Shows icons only (no labels)
```

#### iPhone 14 (390px) - Modern Standard
```
- [ ] Same as iPhone SE
- [ ] Touch targets feel comfortable (44x44px)
- [ ] Typography readable (16px base)
```

#### iPad (768px) - Tablet Breakpoint
```
- [ ] State 1: Side-by-side layout (2 columns)
- [ ] State 2: 2-column grid (Signals + Insights top, Sparks bottom)
- [ ] State 3: 2-column grid
- [ ] State 4: Sidebar still hidden, mobile nav shows
- [ ] Icon navigation: Labels now visible
```

#### iPad Pro (1024px) - Desktop Layout
```
- [ ] State 1: Side-by-side (2 columns)
- [ ] State 2: 3-column layout
- [ ] State 3: 2-column grid
- [ ] State 4: Sidebar visible (240px), hamburger hidden
- [ ] All desktop features active
```

---

## ✋ Touch Interaction Tests

### State 1: Extraction Animation
```
- [ ] No interactive elements (read-only state) ✓
```

### State 2: Three-Column Layout
```
- [ ] Signal card: Tap to view full document (if implemented)
- [ ] Insight card: Tap to download Stage 1 output
- [ ] Spark preview cards: Tap to navigate to State 4
```

### State 3: Sparks Grid
```
- [ ] Spark cards: Tap shows active feedback (scale down)
- [ ] Download All button: ≥44px height, tap feedback
- [ ] New Pipeline button: ≥44px height, tap feedback
- [ ] Icon navigation: Each icon ≥44px touch area
```

### State 4: Detail View
```
Mobile Navigation Bar:
- [ ] Back button: ≥44px, tap feedback (color change)
- [ ] Prev button: ≥44px, disabled when at first spark
- [ ] Next button: ≥44px, disabled when at last spark
- [ ] Counter: Shows "1 of N" (not interactive)

Hamburger Menu:
- [ ] Menu button: ≥44px, visible only on mobile (<1024px)
- [ ] Opens with 300ms slide animation from left
- [ ] Backdrop: Tap to close menu
- [ ] Thumbnails: 2-column grid, tap selects spark
- [ ] Selected spark: Shows teal border

Swipe Gestures:
- [ ] Swipe left (50px min): Navigate to next spark
- [ ] Swipe right (50px min): Navigate to previous spark
- [ ] Vertical swipe: Ignored (scrolls content)
- [ ] Swipe at first spark (right): No action
- [ ] Swipe at last spark (left): No action
```

---

## 📱 iOS-Specific Tests

### Safe Area Insets (iPhone with notch)
```
- [ ] State 4 mobile nav bar: Not hidden behind notch
- [ ] State 4 hamburger menu: Content not hidden by notch
- [ ] Action bar: Not hidden by home indicator
- [ ] Content scrolls correctly with safe areas
```

### Pull-to-Refresh Prevention
```
- [ ] State 2: No bounce when scrolling to top
- [ ] State 4: No bounce when scrolling to top
- [ ] Confirms overscroll-behavior: contain is working
```

---

## 📐 Typography & Spacing Tests

### Mobile (375px - 767px)
```
- [ ] Base font: 16px (readable without zoom)
- [ ] Headings: 18-28px range
- [ ] Line height: 1.5 (comfortable reading)
- [ ] Padding: 16px (comfortable spacing)
- [ ] Grid gaps: 16px (not cramped)
```

### Desktop (1024px+)
```
- [ ] Base font: 18px (or inherited from body)
- [ ] Headings: 20-32px range
- [ ] Line height: 1.6
- [ ] Padding: 24px
- [ ] Grid gaps: 24px
```

---

## 🎨 Visual Polish Tests

### Transitions & Animations
```
- [ ] State transitions: Smooth 300-800ms fades
- [ ] Swipe feedback: Immediate response
- [ ] Hamburger menu: Smooth 300ms slide
- [ ] Active states: Instant tap feedback
- [ ] Button hover (desktop): Smooth color change
```

### Color & Contrast
```
- [ ] Primary teal: #5B9A99 (readable on white)
- [ ] Active states: Darker teal #3A6F6E
- [ ] Disabled buttons: 50% opacity
- [ ] Selected items: Teal border visible
- [ ] Gradients: Visible on all spark cards
```

---

## 🚫 No Horizontal Scroll Test

### Critical Check (All Breakpoints)
```
- [ ] 375px: window.scrollX === 0 after render
- [ ] 390px: No horizontal scrollbar visible
- [ ] 768px: No horizontal scrollbar visible
- [ ] 1024px: No horizontal scrollbar visible

If horizontal scroll detected:
1. Check for fixed widths without max-width
2. Check for negative margins extending beyond viewport
3. Check for absolute positioning outside bounds
4. Verify all images have max-width: 100%
```

---

## 🐛 Common Issues to Watch For

### Layout Issues
```
- [ ] Text overflow: No text breaking layout
- [ ] Image aspect ratios: Maintained on all screens
- [ ] Flexbox gaps: No unintended wrapping
- [ ] Grid columns: Correct count at each breakpoint
```

### Touch Issues
```
- [ ] Double-tap zoom: Disabled (viewport meta)
- [ ] Touch delays: No 300ms click delay
- [ ] Ghost clicks: No double-trigger issues
- [ ] Scroll jank: Smooth 60fps scrolling
```

### State Machine Issues
```
- [ ] State transitions: No flashing/flickering
- [ ] Card selection: Updates immediately
- [ ] Back navigation: Returns to correct state
- [ ] URL sync: History state preserved
```

---

## ⚡ Performance Checks

### Mobile Network Throttling
```
- [ ] Test with Chrome DevTools "Slow 3G"
- [ ] TTI (Time to Interactive): < 3 seconds
- [ ] FCP (First Contentful Paint): < 1 second
- [ ] No layout shifts (CLS: 0)
```

### Animation Performance
```
- [ ] State transitions: No dropped frames
- [ ] Swipe gestures: Responds instantly (<16ms)
- [ ] Hamburger menu: Smooth 60fps animation
- [ ] Scroll performance: Buttery smooth
```

---

## ✅ Final Validation

### Cross-Browser (Mobile)
```
- [ ] iOS Safari: All features work
- [ ] Chrome Android: All features work
- [ ] Firefox Android: All features work
- [ ] Samsung Internet: All features work (if available)
```

### Accessibility (Mobile)
```
- [ ] VoiceOver (iOS): All buttons announced
- [ ] TalkBack (Android): All buttons announced
- [ ] Focus order: Logical tab sequence
- [ ] Aria labels: Descriptive and present
```

### Edge Cases
```
- [ ] Rotate device: Layout adapts immediately
- [ ] Small text zoom: Layout doesn't break
- [ ] Dark mode: Colors still readable (if implemented)
- [ ] Slow device: Animations gracefully degrade
```

---

## 🎯 Success Criteria

**All tests must pass for Story 8.7 completion:**

1. ✅ No horizontal scrolling at any breakpoint
2. ✅ All touch targets ≥44x44px
3. ✅ Typography readable on smallest device (iPhone SE)
4. ✅ Swipe gestures work smoothly
5. ✅ Hamburger menu opens/closes correctly
6. ✅ Safe area insets respected on iPhone notch
7. ✅ No layout shifts or jank during interactions
8. ✅ All 4 states adapt correctly to mobile

**Estimated Testing Time:** 30-45 minutes per device type
