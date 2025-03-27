import React, { useEffect, useState } from "react";
import Menu from "../menu/MainMenu";
import "./TaskList.css";
import ListComponent from "./ListComponent";
import { useNavigate, useParams } from "react-router-dom";
import { MakeAuthorizedRequest, MakeRequest } from "../../../../API/RequestService";
import TokenController from "../../../../controllers/TokenController";

const TaskList = () => {
  let navigate = useNavigate(); 
  const { id } = useParams();

  const routeChange = () => { 
    let path = `/contest/${id}/standings`; 
    navigate(path);
  }

  const [problems, setProblems] = useState([]);

  useEffect(() => {
    async function handleProblems() {
      let requestOptions = {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': TokenController.getToken()
        },
        credentials: 'include'
      };
      let response = await MakeAuthorizedRequest(`contest/${id}`, requestOptions)
      if (response.status == 403 || (response.status === 500 && response.data.message === "Token is expired")) {
        navigate("/contests")
      } else {
        setProblems(response.data.problems)
      }
    }
    if (id !== undefined) {
      handleProblems();
    }
  }, [id]);


  return (
    <div className="app-wrapper">
      <Menu/>
      <div className="info">
        <div className="taskListForm">
          <p className="taskHeader">Задачи:</p>
          {problems && problems.length > 0 ? (
            problems.map((problem, index) => (
                <ListComponent key={problem.id} problemId = {problem.id} task={problem.properties} counter={String.fromCharCode(65 + index)} />
            ))
            ) : (
            <p>Нет доступных задач.</p>
            )}
        </div>
        <button className="standingButton" onClick={routeChange}>Таблица результатов</button>
      </div>
    </div>
  )
}

export default TaskList;
