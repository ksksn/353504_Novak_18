import React, { useEffect } from 'react';
function Latex(props) {
  let node = React.createRef();
  useEffect(() => {
    renderMath();
  });
  const renderMath = () => {
    window.MathJax.Hub.Queue([
      "Typeset", 
      window.MathJax.Hub,
      node.current
   ],
   ["resetEquationNumbers",window.MathJax.InputJax.TeX]);
  }
  return (
    <div ref={node}>
      {props.children}
    </div>
  );
}
export default Latex;