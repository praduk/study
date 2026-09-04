/** Use a resolved entry's title while preserving literal text until resolution. */
export function referenceDisplayText(
  literalTag: string,
  title: string | undefined,
): string {
  return title?.trim() ? title : literalTag;
}
