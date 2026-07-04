import { useLayoutEffect, useRef, useState } from "react";
import styles from "./SlidingText.module.css";

interface SlidingTextProps {
  text: string;
  hoverSelector: string;
  animationDuration?: number;
  className?: string;
}

/**
 * A component that displays text, truncates it with an ellipsis if it overflows,
 * and slides the full text on hover of a specified parent selector.
 *
 * @param {object} props
 * @param {string} props.text - The text content to display.
 * @param {string} props.hoverSelector - A CSS selector for the ancestor element that triggers the animation on hover. e.g., ".card-container"
 * @param {number} [props.animationDuration=5] - The duration of the sliding animation in seconds.
 * @param {string} [props.className] - Optional custom class for the container.
 */
const SlidingText = ({
  text,
  hoverSelector,
  animationDuration = 5,
  className = "",
}: SlidingTextProps) => {
  // State to track if the text is actually overflowing its container.
  const [isOverflowing, setIsOverflowing] = useState(false);

  // State to store the exact pixel amount of overflow to be used in CSS transform.
  const [transformOffset, setTransformOffset] = useState(0);

  // Refs to get direct access to the DOM elements for measurement.
  const containerRef = useRef<HTMLDivElement | null>(null);
  // Variable holding textRef
  const textRef = useRef<HTMLSpanElement | null>(null);

  // useLayoutEffect runs synchronously after all DOM mutations.
  // It's preferred over useEffect for DOM measurements to avoid visual flickering.
  useLayoutEffect(() => {
    // Variable holding container
    const container = containerRef.current;
    // Variable holding textElement
    const textElement = textRef.current;

    if (container && textElement) {
      // scrollWidth is the total width of the content, even if not visible.
      // clientWidth is the visible width of the container.
      const hasOverflow = textElement.scrollWidth > container.clientWidth;
      setIsOverflowing(hasOverflow);

      if (hasOverflow) {
        // Calculate the exact amount the text needs to move to show its end.
        const offset = container.clientWidth - textElement.scrollWidth;
        setTransformOffset(offset);
      }
    }
  }, [text]); // Re-run this logic whenever the text prop changes.

  // Dynamically generate the CSS rule for the hover effect.
  // This is the key to making the hover trigger customizable via props.
  const dynamicHoverStyle = `
    ${hoverSelector}:hover .${styles.slidingText} {
      animation: ${styles.slide} ${animationDuration}s linear infinite alternate;
    }
  `;

  return (
    <>
      {/* 
        Only inject the style tag if text is overflowing.
        This is an optimization to avoid adding unnecessary styles to the DOM.
      */}
      {isOverflowing && <style>{dynamicHoverStyle}</style>}

      <div
        ref={containerRef}
        className={`${styles.container} ${className}`}
        style={
          {
            // Pass the calculated offset to CSS via a custom property (variable).
            "--transform-offset": `${transformOffset}px`,
          } as React.CSSProperties
        }
      >
        <span
          ref={textRef}
          // Apply the 'slidingText' class only if overflowing, otherwise it's just static.
          className={isOverflowing ? styles.slidingText : styles.staticText}
        >
          {text}
        </span>
      </div>
    </>
  );
};

export default SlidingText;
