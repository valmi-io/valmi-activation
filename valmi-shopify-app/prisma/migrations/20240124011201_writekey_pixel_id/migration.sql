/*
  Warnings:

  - Added the required column `writeKey` to the `webPixel` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_webPixel" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "writeKey" TEXT NOT NULL
);
INSERT INTO "new_webPixel" ("id") SELECT "id" FROM "webPixel";
DROP TABLE "webPixel";
ALTER TABLE "new_webPixel" RENAME TO "webPixel";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
