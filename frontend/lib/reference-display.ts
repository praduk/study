/** Use an explicit label, then a resolved title, while preserving literal text as fallback. */
export function referenceDisplayText(
  literalTag: string,
  title: string | undefined,
  replacementText?: string,
): string {
  return replacementText?.trim() || title?.trim() || literalTag;
}
