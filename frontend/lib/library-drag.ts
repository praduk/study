import type { DragEvent } from 'react';

export const LIBRARY_DRAG_TYPE = 'application/x-study-item';

// Accept on dragenter as well as dragover: a quick drop can arrive before
// the browser dispatches a dragover on the final target.
export function acceptLibraryDrag(event: DragEvent<HTMLElement>) {
  if (!event.dataTransfer.types.includes(LIBRARY_DRAG_TYPE)) return;
  event.preventDefault();
  event.stopPropagation();
  event.dataTransfer.dropEffect = 'move';
  event.currentTarget.classList.add('drop-target');
}
