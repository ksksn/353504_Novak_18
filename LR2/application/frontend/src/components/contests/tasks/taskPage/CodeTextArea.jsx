import React from "react";
import CodeMirror from "@uiw/react-codemirror";

export default function CodeInput() {
  const onChange = React.useCallback((value, viewUpdate) => {
    console.log("value:", value);
  }, []);
  return (
    <div>
    <CodeMirror
      value="Наберите код..."
      height="200px"
      paddingBottom = "10px"
      readOnly={false}
      onChange={(value, viewUpdate) => {
        console.log("value:", value);
      }}
    />
    </div>
  );
}