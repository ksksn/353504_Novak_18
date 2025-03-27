import React from "react";
import "./styles/Date.css";
import "./styles/FieldForm.css";
import name from "./styles/ContestsName.module.css";

const ContestsComponent = (props) => {
  const handleOnClick = () => {
    if (props.onClick) {
      props.onClick();
    }
  };

  return (
    <div className="fieldForm" onClick={handleOnClick}>
      <h1 className={name.contestsName}> {props.contest} </h1>
      <p className="date"> {props.date} </p>
    </div>
  );
};

export default ContestsComponent;
