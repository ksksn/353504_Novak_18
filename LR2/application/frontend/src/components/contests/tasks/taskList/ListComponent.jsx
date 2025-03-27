import React from "react"
import "./TaskList.css"
import { useNavigate } from "react-router-dom"

const ListComponent = (props) => {
  let navigate = useNavigate(); 

  const routeChange = () =>{ 
    let path = `/submissions/${props.problemId}`; 
    navigate(path);
  }
    return(
        <div>
            <div className="taskNameList">
                {props.counter}. {props.task.name }
                <button className="mysollution" onClick={routeChange}> Мои решения </button>
            </div>
            <p className="line"/>
        </div>
    )
}

export default ListComponent