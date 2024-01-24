/*
  Warnings:

  - Added the required column `host` to the `WebPixel` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_WebPixel" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "writeKey" TEXT NOT NULL,
    "host" TEXT NOT NULL
);
INSERT INTO "new_WebPixel" ("id", "writeKey") SELECT "id", "writeKey" FROM "WebPixel";
DROP TABLE "WebPixel";
ALTER TABLE "new_WebPixel" RENAME TO "WebPixel";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
