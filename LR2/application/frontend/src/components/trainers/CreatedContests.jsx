import React, { useState } from "react";
import "../contests/tasks/taskList/TaskList.css";
import { useNavigate } from "react-router-dom";
import "./styles/Button.css";
import "./styles/ModalContest.css";
import ContestService from "../../API/ContestService";

const CreatedContests = (props) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [file, setFile] = useState(null);

  let navigate = useNavigate();

  const routeChange = () => {
    let path = `/contests/1/problem/standings`;
    navigate(path);
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    // Handle the file upload logic here
    await ContestService.addProblem(file, props.contestId)  
    setModalVisible(false);
  };

  const closeModal = () => {
    setFile(null);
    setModalVisible(false);
  };

  return (
    <div>
      <div className="taskNameList">
        <span className="contestHeader">{props.contestName}</span>
        <button className="mysollution" onClick={() => setModalVisible(true)}>
          Добавить задачу
        </button>
        <button className="lightButton" onClick={routeChange}>
          Таблица результатов
        </button>
      </div>
      <p className="line" />

      {modalVisible && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={closeModal}>
              &times;
            </span>
            <h2 className="header">Загрузите zip-файл</h2>
            <input type="file" onChange={handleFileChange} />
            <button className="darkButton" onClick={handleUpload}>
              Загрузить
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreatedContests;
