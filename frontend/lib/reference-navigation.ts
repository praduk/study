interface VariantLike {
  id: string;
  main: boolean;
}

export interface EntryVariants {
  formulations: VariantLike[];
  supplements: VariantLike[];
}

export interface ReadingVariantSelection {
  formulationId: string;
  supplementId: string | null;
}

/** Resolve an exact reference target without guessing an unknown variant ID. */
export function readingVariantSelection(
  entry: EntryVariants,
  requestedVariantId: string | null,
): ReadingVariantSelection {
  const requestedFormulation = entry.formulations.find(
    (variant) => variant.id === requestedVariantId,
  );
  const requestedSupplement = entry.supplements.find(
    (variant) => variant.id === requestedVariantId,
  );
  const mainFormulation =
    entry.formulations.find((variant) => variant.main) ?? entry.formulations[0];

  return {
    formulationId: requestedFormulation?.id ?? mainFormulation?.id ?? '',
    supplementId: requestedSupplement?.id ?? null,
  };
}
