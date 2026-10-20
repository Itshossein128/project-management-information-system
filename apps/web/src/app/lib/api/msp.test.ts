import test from "node:test";
import assert from "node:assert/strict";
import {
  isMspFamilyFile,
  isP6File,
  isScheduleImportFile,
} from "./msp-file-utils.ts";

function fakeFile(name: string): { name: string } {
  return { name };
}

test("routes xer to P6 and mpp/xml to MSP family", () => {
  assert.equal(isP6File(fakeFile("a.xer")), true);
  assert.equal(isP6File(fakeFile("a.mpp")), false);
  assert.equal(isMspFamilyFile(fakeFile("a.mpp")), true);
  assert.equal(isMspFamilyFile(fakeFile("a.xml")), true);
  assert.equal(isMspFamilyFile(fakeFile("a.xer")), false);
  assert.equal(isScheduleImportFile(fakeFile("plan.mpp")), true);
  assert.equal(isScheduleImportFile(fakeFile("plan.txt")), false);
});
