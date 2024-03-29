/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

const setDataAtCurrentPath = (
  sourcedata: any[],
  mappeddata: any,
  currentPath: any[],
  arrayIdx: number,
  key: string
) => {
  if (sourcedata.length > 0) {
    let x = [mappeddata];
    for (let i = 0; i < currentPath.length; i++) {
      x = x.flatMap((obj) => {
        if (obj && obj.hasOwnProperty(currentPath[i])) {
          return obj[currentPath[i]];
        }
        else return undefined;
      });
      x = x.filter((el: any) => el !== undefined);
    }
    for (let i = 0; i < x.length; i++) {
      if (sourcedata.length <= i) {
        x[i][key] = ""; // setting empty string
      } else {
        x[i][key] = sourcedata[i];
      }
    }
  }
};

const checkForPropertyAtPath = (
  mappeddata: any,
  currentPath: any[],
  arrayIdx: number,
  key: string
) => {
  // go to the end
  let x = mappeddata;
  for (let i = 0; i < currentPath.length; i++) {
    //console.log(key, x, currentPath);
    if (arrayIdx == i) {
      if(x && x.hasOwnProperty(currentPath[i]) && Array.isArray(x[currentPath[i]]) && x[currentPath[i]].length > 0)
        x = x[currentPath[i]][0];
      else return false;
    } else {
      if (!x || !x.hasOwnProperty(currentPath[i])) return false;
        x = x[currentPath[i]];
    }
  }
  if (x.hasOwnProperty(key)) return true;
  return false;
};

export const splitJPpath = (p: string) => {
  let path: any = p.split(".");
  //console.log(path);
  path = path.flatMap((el: string) => {
    if (el.endsWith("[*]")) {
      return [
        { expression: { type: "identifier", value: el.slice(0,el.length-3)} },
        { expression: { type: "wildcard", value: "*" } },
      ];
    } else if (el !== "$"){
      return { expression: { type: "identifier", value: el } };
    }
  });
  //console.log(path);
  path = path.filter((el: any) => el !== undefined);
  return path;
};


export const query = (obj: any, p: string) => {
  try {
    let path: any = splitJPpath(p);
    let objs = [obj];
    for (let i = 0; i < path.length; i++) {
      const element = path[i];
      if (element.expression.type == "identifier") {
        if (
          i < path.length - 1 &&
          path[i + 1].expression.type == "wildcard" &&
          path[i + 1].expression.value == "*"
        ) {
          objs = objs.flatMap((el: any) => {
            if (el && el.hasOwnProperty(element.expression.value)) {
              return el[element.expression.value];
            }
            else return undefined;
          });
          objs = objs.filter((el: any) => el !== null);
        } else {
          objs = objs.map((el: any) => {
            if (el && el.hasOwnProperty(element.expression.value)) {
              return el[element.expression.value];
            }
            else return undefined;
          });
          objs = objs.filter((el: any) => el !== undefined);
        }
      }
    }
    return objs;
  } catch (e) {
    console.log("error", e);
    return [];
  }
};

// build the mappeddata structure --  only one wildcard supported.
export const setDataForJsonPath = (
  sourcedata: any[],
  mappeddata: any,
  pathexp: string
) => {
  // crossing limit of ui extension.. so writing my own
  //var path = JSONPath.parse(pathexp);
  let path : any = splitJPpath(pathexp);

  const currentPath = [];
  let arrayIdx = -1;
  for (var idx = 0; idx < path.length; idx++) {
    const element = path[idx];
    if (element.expression.type == "identifier") {
      if (idx < path.length - 1) {
        if (
          checkForPropertyAtPath(
            mappeddata,
            currentPath,
            arrayIdx,
            element.expression.value
          )
        ) {
        } else {
          if (
            idx < path.length - 1 &&
            path[idx + 1].expression.type == "wildcard" &&
            path[idx + 1].expression.value == "*"
          ) {
            setDataAtCurrentPath(
              [
                sourcedata.map((el) => {
                  return {};
                }),
              ], //setting an  array with empty objects
              mappeddata,
              currentPath,
              arrayIdx,
              element.expression.value
            );
          } else {
            setDataAtCurrentPath(
              [{}], //setting an empty object
              mappeddata,
              currentPath,
              arrayIdx,
              element.expression.value
            );
          }
        }
        currentPath.push(element.expression.value);
      } else {
        setDataAtCurrentPath(
          sourcedata,
          mappeddata,
          currentPath,
          arrayIdx,
          element.expression.value
        );
      }
    } else if (
      element.expression.type == "wildcard" &&
      element.expression.value == "*"
    ) {
      arrayIdx = currentPath.length - 1;
    }
  }
};