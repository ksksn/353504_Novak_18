import React from "react";
import "./headForm.css";
import style from "./styles/Name.module.css";
import navigateStyle from "./styles/Navigate.module.css";
import { NavLink } from 'react-router-dom';

const Header = () => {
    return(
    <header className='headForm'>
        <NavLink to = "/" className={style.name}> BetterSolve</NavLink>
        <div  className={navigateStyle.navigationBar}>
            <div>
            <NavLink to = "/" className = { navData => navData.isActive ? navigateStyle.active : ''}>  Главная </NavLink>
            </div>

            <div>
            <NavLink to = "/contests" className = { navData => navData.isActive ? navigateStyle.active : ''}>  Соревнования </NavLink>
            </div>

            <div>
            <NavLink to = "/edu" className = { navData => navData.isActive ? navigateStyle.active : ''}>  Преподавателям </NavLink>
            </div>

            <div>
            <NavLink to = "/admin" className = { navData => navData.isActive ? navigateStyle.active : ''}>  Администраторам </NavLink>
            </div>

            <div className={navigateStyle.authLinks}>
            <NavLink to = "/enter" className = { navData => navData.isActive ? navigateStyle.active : ''}>  Вход </NavLink>
            </div>
            <div className={navigateStyle.palka}>|</div>
            <div className={navigateStyle.authLinks}>
            <NavLink to = "/register" className = { navData => navData.isActive ? navigateStyle.active : ''} >  Регистрация </NavLink>
            </div>
            
        </div>
    </header>)
}
export default Header