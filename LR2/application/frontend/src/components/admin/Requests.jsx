import React from "react";
import "../contests/tasks/taskList/TaskList.css";
import "../trainers/styles/Button.css";

const Requests = (props) => {
    return(
        <div>
            <div className="taskNameList">
                <span className="contestHeader">{props.nickname}</span>
                <button className="darkButton"> Подтвердить </button>
                <button className="lightButton"> Отклонить </button>
            </div>
            <p className="line"/>
        </div>
    )
}

export default Requests