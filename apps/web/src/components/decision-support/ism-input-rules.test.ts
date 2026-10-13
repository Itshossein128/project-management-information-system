import test from "node:test";
import assert from "node:assert/strict";
import {
  createIsmMatrix,
  editIsmCell,
  hydrateIsmMatrix,
  validateIsmDraft,
  selectIsmValue,
} from "./ism-input-rules.ts";

test("explicit zero diagonal and unanswered cross-pairs", () => {
  assert.deepEqual(createIsmMatrix(2), [
    [0, null],
    [null, 0],
  ]);
  assert.deepEqual(createIsmMatrix(0), []);
});
test("exact options and independent opposite direction", () => {
  assert.equal(selectIsmValue(""), null);
  assert.equal(selectIsmValue("0"), 0);
  assert.equal(selectIsmValue("1"), 1);
  assert.throws(() => selectIsmValue("true"));
  assert.deepEqual(
    editIsmCell(
      [
        [0, 0],
        [1, 0],
      ],
      0,
      1,
      null,
    ),
    [
      [0, null],
      [1, 0],
    ],
  );
});
test("invalid raw hydration is retained, empty legacy initializes only new draft", () => {
  for (const value of [4, [[true, "1"]], [["bad"]], [[9]], null])
    assert.deepEqual(hydrateIsmMatrix(value, 2), value);
  assert.deepEqual(hydrateIsmMatrix([], 2), [
    [0, null],
    [null, 0],
  ]);
});
test("strict local errors do not compute derived analysis", () => {
  assert.deepEqual(validateIsmDraft(["A"], [[0]]), []);
  assert.deepEqual(validateIsmDraft(["A"], [[1]]), []);
  for (const [v, code] of [
    [null, "cell_empty"],
    [true, "non_numeric"],
    ["0", "non_numeric"],
    [0.5, "ism_relation_invalid"],
    [Infinity, "non_finite"],
  ] as const) {
    assert.equal(validateIsmDraft(["A"], [[v]])[0]?.code, code);
    assert.equal(validateIsmDraft(["A"], [[v]])[0]?.path, "ism_matrix.0.0");
  }
  assert.equal(
    validateIsmDraft(
      ["A", "A"],
      [
        [0, 0],
        [0, 0],
      ],
    )[0]?.code,
    "name_duplicate",
  );
  assert.equal(validateIsmDraft([], [])[0]?.code, "dimension_invalid");
  assert.equal(
    validateIsmDraft(["A"], [[0], [0]])[0]?.code,
    "dimension_invalid",
  );
});

import { remapIsmMatrix } from "./ism-input-rules.ts";
test("operation identity remaps both axes without guessing renamed strings", () => {
  const matrix = [
    [0, 1, 0],
    [0, 1, 1],
    [1, 0, 0],
  ];
  assert.deepEqual(
    remapIsmMatrix(matrix, 3, { kind: "rename", index: 0 }),
    matrix,
  );
  assert.deepEqual(
    remapIsmMatrix(matrix, 3, { kind: "move", from: 1, to: 0 }),
    [
      [1, 0, 1],
      [1, 0, 0],
      [0, 1, 0],
    ],
  );
  assert.deepEqual(remapIsmMatrix(matrix, 4, { kind: "add", index: 1 }), [
    [0, null, 1, 0],
    [null, 0, null, null],
    [0, null, 1, 1],
    [1, null, 0, 0],
  ]);
  assert.deepEqual(remapIsmMatrix(matrix, 2, { kind: "remove", index: 1 }), [
    [0, 0],
    [1, 0],
  ]);
  assert.equal(remapIsmMatrix(9, 2, { kind: "rename", index: 0 }), 9);
});
