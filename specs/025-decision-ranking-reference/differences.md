# Ranking Sample and Product Differences

The original sample remains unchanged and editable in [document 09](../../docs/decision-support/09-ranking-reference.md). These are existing product additions, not a replacement reference contract. The sample implements only SAW/TOPSIS, always together, and never establishes full product acceptance.

| Category | Preserved sample | Existing product and evidence |
| --- | --- | --- |
| Normalized weights | Normalizes internally; does not return a separate vector | Independent engines return and records retain normalized alongside raw weights. Twelve analytical parity cases assert this product-only vector. |
| Numeric ranks | Sorted lists with both method scores, no numeric rank | One-based interim ordinal rank; exact ties retain input order. Case tests and fresh actual API disagreement/tie/history checks preserve this behavior. |
| TOPSIS distances | Calculates distances internally but returns only scores/order | Records/results retain best/worst distances, closeness and score alias. New checks assert finite nonnegative distances/alias; existing TOPSIS tests separately verify the analytical distance behavior. Sample score agreement is not distance proof. |
| Errors | Plain ValueError/TypeError conversion exceptions without field/cell location | Located CodedValidationError issues and localized named feedback. 35 invalid cases assert relevant paths/codes, including SAW benefit-column versus TOPSIS denominator mapping; fresh API and reused EN/FA feedback checks cover other layers. |
| Execution | Each call calculates both methods | Selected method executes independently with manual weights; no other method prerequisite, blended rank or automatic weight transfer. Fresh method-only and real disagreement tests verify this. |
| History | No form, persistence or provenance | Authorized distinct immutable records with inputs/results/initiator/time. Fresh API immutability/access checks and verified reused real EN/FA historical keyboard review establish this product behavior. |

O01/O02 remain open as **final product policy**; current precision, ordinal ties and TOPSIS distance fields are preserved. No old result is rounded, re-ranked or rewritten by this feature. No AHP/DEMATEL/ISM calculation is inferred from the sample.

Representation differences are characterized, not standardized anew: numeric strings and boolean weights currently convert in both layers; boolean matrix cells are sample-only; trimmed duplicate names, None names and trimmed type strings differ. The seven explicit probe outcomes are in validation-reference.json. O03/O04 remain owned by the input specification/source review.

Ordinary comparisons use bounded numeric fixtures and absolute 1e-9 with zero relative tolerance. Extremely large/small finite arithmetic and localized conversions are not universal parity claims. Tolerance does not group near ties or change display precision.

Evidence: [fresh reference observations](validation-reference.json), [fresh backend checks](evidence/backend.txt), [browser reuse provenance](evidence/browser-provenance.json), and [requirement reconciliation](validation.md). Browser disagreement fixtures show presentation only and are paired with real backend calculations. Reused evidence is identified explicitly; no new browser execution is claimed.
