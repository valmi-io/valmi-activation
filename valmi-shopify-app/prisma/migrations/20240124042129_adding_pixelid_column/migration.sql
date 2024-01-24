/*
  Warnings:

  - You are about to drop the column `host` on the `WebPixel` table. All the data in the column will be lost.
  - You are about to drop the column `writeKey` on the `WebPixel` table. All the data in the column will be lost.
  - Added the required column `pixel_id` to the `WebPixel` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_WebPixel" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "pixel_id" TEXT NOT NULL
);
INSERT INTO "new_WebPixel" ("id") SELECT "id" FROM "WebPixel";
DROP TABLE "WebPixel";
ALTER TABLE "new_WebPixel" RENAME TO "WebPixel";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
