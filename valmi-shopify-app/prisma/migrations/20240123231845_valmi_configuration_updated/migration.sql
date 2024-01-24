/*
  Warnings:

  - The primary key for the `Valmiconf` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `Valmiconf` table. All the data in the column will be lost.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Valmiconf" (
    "host" TEXT NOT NULL PRIMARY KEY,
    "writeKey" TEXT NOT NULL
);
INSERT INTO "new_Valmiconf" ("host", "writeKey") SELECT "host", "writeKey" FROM "Valmiconf";
DROP TABLE "Valmiconf";
ALTER TABLE "new_Valmiconf" RENAME TO "Valmiconf";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
