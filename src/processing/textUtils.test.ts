import { describe, expect, it } from "vitest";
import { strToPostScript, strToSubscriptString } from "./textUtils";

describe("test processing textUtils", () => {
  it("test strToSubscriptString full conversion", () => {
    const originalStr = "hello123";
    const finalStr = strToSubscriptString(originalStr);
    expect(finalStr).toBe("ₕₑₗₗₒ₁₂₃");
  });

  it("test strToSubscriptString fail conversion", () => {
    const originalStr = "hello123!";
    const finalStr = strToSubscriptString(originalStr);
    expect(finalStr).toBe("hello123!");
  });

  it("test strToPostScript full conversion", () => {
    const originalStr = "hello123";
    const finalStr = strToPostScript(originalStr);
    expect(finalStr).toBe("ʰᵉˡˡᵒ¹²³");
  });

  it("test strToPostScript fail conversion", () => {
    const originalStr = "hello123!";
    const finalStr = strToPostScript(originalStr);
    expect(finalStr).toBe("hello123!");
  });
});
